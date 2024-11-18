package com.onetry.spring.user.dto.res;

import com.onetry.spring.user.entity.User;
import lombok.Builder;

@Builder
public record UserInfoResDto(
        Long id,
        String name,
        String email,
        String profileImgUrl
) {
    public static UserInfoResDto from(User user){
        return UserInfoResDto.builder()
                .id(user.getId())
                .name(user.getName())
                .email(user.getEmail())
                .profileImgUrl(user.getProfileFilePath())
                .build();
    }
}